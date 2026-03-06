from abc import abstractmethod
from typing import Protocol

from piaps.domain.entities.user import User


class IIdentityProvider(Protocol):
    @abstractmethod
    async def get_user(self) -> User: ...
