from piaps.application.errors.auth import AuthenticationError, InvalidTokenError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.auth.jwt_provider import IJWTProvider, TokenData, TokenType
from piaps.application.interfaces.readers.user import IUserReader
from piaps.domain.entities.user import User


class IdentityProvider(IIdentityProvider):
    def __init__(
        self,
        token: str,
        jwt_provider: IJWTProvider,
        user_reader: IUserReader,
    ) -> None:
        self._token: str = token
        self._jwt_provider: IJWTProvider = jwt_provider
        self._user_reader: IUserReader = user_reader
        self._cached_user: User | None = None

    async def get_user(self) -> User:
        if self._cached_user is not None:
            return self._cached_user

        user: User = await self._get_user_from_token()
        self._cached_user = user
        return user

    async def _get_user_from_token(self) -> User:
        decoded: TokenData = self._jwt_provider.decode_token(self._token)

        if decoded.meta.type != TokenType.ACCESS:
            raise InvalidTokenError(f"Token type must be '{TokenType.ACCESS}'")

        user: User | None = await self._user_reader.find_by_id(decoded.payload.sub)

        if user is None:
            raise AuthenticationError("User no longer exists")

        return user
