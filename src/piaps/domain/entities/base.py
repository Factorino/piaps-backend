from abc import ABC
from collections.abc import Hashable
from dataclasses import dataclass
from typing import Any, Self, dataclass_transform


@dataclass_transform(kw_only_default=True)
def entity[ClsT](cls: type[ClsT]) -> type[ClsT]:
    return dataclass(cls, slots=True, kw_only=True)


@entity
class Entity[IdT: Hashable](ABC):
    id: IdT

    def __new__(cls, *_args: Any, **_kwargs: Any) -> Self:
        if cls is Entity:
            raise TypeError("Base Entity cannot be instantiated directly")
        return object.__new__(cls)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "id" and getattr(self, "id", None) is not None:
            raise AttributeError("Changing entity ID is not permitted")
        return object.__setattr__(self, name, value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return other.id == self.id

    def __hash__(self) -> int:
        return hash((type(self), self.id))
