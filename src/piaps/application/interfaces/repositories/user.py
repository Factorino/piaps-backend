from abc import abstractmethod
from typing import Protocol

from piaps.domain.entities.user import User


class IUserRepository(Protocol):
    @abstractmethod
    async def add(self, entity: User) -> User: ...

    @abstractmethod
    async def update(self, entity: User) -> User: ...

    @abstractmethod
    async def delete(self, entity: User) -> None: ...
