from abc import abstractmethod
from typing import Protocol

from piaps.domain.value_objects.password import Password


class IPasswordHasher(Protocol):
    @abstractmethod
    def hash_password(self, password: Password) -> bytes: ...

    @abstractmethod
    def verify_password(self, raw: str, hashed: bytes) -> bool: ...
