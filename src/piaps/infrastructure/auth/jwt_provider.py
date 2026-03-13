from datetime import UTC, datetime, timedelta
import json
from typing import Any

import jwt
from pydantic import TypeAdapter

from piaps.application.errors.auth import InvalidTokenError, TokenExpiredError
from piaps.application.errors.base import DataMapperError, OperationFailedError
from piaps.application.interfaces.auth.jwt_provider import (
    IJWTProvider,
    TokenData,
    TokenMeta,
    TokenPayload,
    TokenType,
)


_adapter: TypeAdapter[TokenData] = TypeAdapter(TokenData)


class PyJWTProvider(IJWTProvider):
    def __init__(
        self,
        public_key: str,
        private_key: str,
        algorithm: str,
        access_ttl: int,
        refresh_ttl: int,
    ) -> None:
        self._public_key: str = public_key
        self._private_key: str = private_key
        self._algorithm: str = algorithm
        self._access_ttl: int = access_ttl
        self._refresh_ttl: int = refresh_ttl

    def create_access_token(self, payload: TokenPayload) -> str:
        return self._create_token(payload, TokenType.ACCESS)

    def create_refresh_token(self, payload: TokenPayload) -> str:
        return self._create_token(payload, TokenType.REFRESH)

    def decode_token(self, token: str) -> TokenData:
        try:
            token_data: dict[str, Any] = jwt.decode(
                token,
                key=self._public_key,
                algorithms=[self._algorithm],
            )
        except jwt.ExpiredSignatureError as e:
            raise TokenExpiredError("Token has expired") from e
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError("Token is invalid") from e

        try:
            return _adapter.validate_python(token_data)
        except Exception as e:
            raise DataMapperError from e

    def _create_token(self, payload: TokenPayload, token_type: TokenType) -> str:
        now: datetime = datetime.now(tz=UTC)
        ttl_minutes: int = (
            self._access_ttl if token_type == TokenType.ACCESS else self._refresh_ttl
        )
        exp = int((now + timedelta(minutes=ttl_minutes)).timestamp())

        token_data = TokenData(
            payload=payload,
            meta=TokenMeta(
                type=token_type,
                iat=int(now.timestamp()),
                exp=exp,
            ),
        )

        try:
            data_bytes: bytes = _adapter.dump_json(token_data)
            data: dict[str, Any] = json.loads(data_bytes)
        except Exception as e:
            raise DataMapperError from e

        try:
            return jwt.encode(
                data,
                key=self._private_key,
                algorithm=self._algorithm,
            )
        except jwt.PyJWTError as e:
            raise OperationFailedError from e
