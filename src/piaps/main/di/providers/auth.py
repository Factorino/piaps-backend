from dishka import BaseScope, Provider, Scope, provide
from fastapi import Request

from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.auth.jwt_provider import IJWTProvider
from piaps.application.interfaces.auth.password_hasher import IPasswordHasher
from piaps.application.interfaces.readers.user import IUserReader
from piaps.infrastructure.auth.identity_provider import IdentityProvider
from piaps.infrastructure.auth.jwt_provider import PyJWTProvider
from piaps.infrastructure.auth.password_hasher import BcryptPasswordHasher
from piaps.main.config.jwt import JWTConfig


class AuthProvider(Provider):
    scope: BaseScope | None = Scope.APP

    @provide
    def password_hasher(self) -> IPasswordHasher:
        return BcryptPasswordHasher()

    @provide
    def jwt_provider(self, config: JWTConfig) -> IJWTProvider:
        return PyJWTProvider(
            public_key=config.public_key,
            private_key=config.private_key,
            algorithm=config.algorithm,
            access_ttl=config.access_ttl_minutes,
            refresh_ttl=config.refresh_ttl_minutes,
        )

    @provide(scope=Scope.REQUEST)
    def identity_provider(
        self,
        request: Request,
        jwt_provider: IJWTProvider,
        user_reader: IUserReader,
    ) -> IIdentityProvider:
        token: str = request.headers.get("Authorization", "").removeprefix("Bearer ")
        return IdentityProvider(
            token=token,
            jwt_provider=jwt_provider,
            user_reader=user_reader,
        )
