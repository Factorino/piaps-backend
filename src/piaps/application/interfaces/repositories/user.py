from abc import abstractmethod
from typing import Protocol

from piaps.domain.entities.user import User, UserId


class IUserRepository(Protocol):
    @abstractmethod
    async def add(self, entity: User) -> None: ...

    @abstractmethod
    async def update(self, entity: User) -> None: ...

    @abstractmethod
    async def delete(self, id: UserId) -> None: ...
