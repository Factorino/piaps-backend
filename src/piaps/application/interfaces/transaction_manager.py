from abc import abstractmethod
from typing import Protocol


class TransactionManager(Protocol):
    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def flush(self) -> None: ...

    @abstractmethod
    def rollback(self) -> None: ...
