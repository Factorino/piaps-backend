from typing import TYPE_CHECKING

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.views.user import UserView
from piaps.application.errors.auth import InvalidCredentialsError
from piaps.application.interfaces.auth.jwt_provider import IJWTProvider, TokenPayload
from piaps.application.interfaces.auth.password_hasher import IPasswordHasher
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.readers.user import IUserReader
from piaps.domain.errors.base import ValidationError
from piaps.domain.value_objects.username import Username


if TYPE_CHECKING:
    from piaps.domain.entities.user import User


@dto
class LoginUserRequest:
    username: str
    password: str


@dto
class LoginUserResponse:
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"  # noqa: S105
    user: UserView


class LoginUser(Interactor[LoginUserRequest, LoginUserResponse]):
    def __init__(
        self,
        user_reader: IUserReader,
        password_hasher: IPasswordHasher,
        jwt_provider: IJWTProvider,
    ) -> None:
        self._user_reader: IUserReader = user_reader
        self._password_hasher: IPasswordHasher = password_hasher
        self._jwt_provider: IJWTProvider = jwt_provider

    async def execute(self, request: LoginUserRequest) -> LoginUserResponse:
        exception = InvalidCredentialsError("Invalid username or password")

        try:
            username = Username(value=request.username)
        except ValidationError:
            raise exception from None

        user: User | None = await self._user_reader.find_by_username(username)
        if user is None:
            raise exception

        if not self._password_hasher.verify_password(request.password, user.password_hash):
            raise exception

        payload = TokenPayload(sub=user.id, role=user.role)
        access_token: str = self._jwt_provider.create_access_token(payload)
        refresh_token: str = self._jwt_provider.create_refresh_token(payload)

        return LoginUserResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserView.from_domain(user),
        )
