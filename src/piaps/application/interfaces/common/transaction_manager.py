from abc import abstractmethod
from typing import Protocol


class ITransactionManager(Protocol):
    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
