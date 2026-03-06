from abc import abstractmethod
from enum import StrEnum
from typing import Protocol

from piaps.application.common.dto.base import dto
from piaps.domain.entities.user import UserId
from piaps.domain.enums.user_role import UserRole


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


@dto
class TokenPayload:
    sub: UserId
    role: UserRole


@dto
class TokenMeta:
    type: TokenType
    iat: int
    exp: int


@dto
class TokenData(TokenPayload, TokenMeta):
    pass


class IJWTProvider(Protocol):
    @abstractmethod
    def create_access_token(self, payload: TokenPayload) -> str: ...

    @abstractmethod
    def create_refresh_token(self, payload: TokenPayload) -> str: ...

    @abstractmethod
    def decode_token(self, token: str) -> TokenData: ...
