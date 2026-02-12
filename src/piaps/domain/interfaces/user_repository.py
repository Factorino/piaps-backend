from abc import abstractmethod
from typing import Protocol
from uuid import UUID

from piaps.domain.entities.user import User


class IUserRepository(Protocol):
    @abstractmethod
    async def find_by_id(self, id: UUID) -> User | None: ...

    @abstractmethod
    async def add(self, entity: User) -> User: ...

    @abstractmethod
    async def update(self, entity: User) -> User: ...

    @abstractmethod
    async def delete(self, entity: User) -> None: ...
