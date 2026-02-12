from abc import ABC
from dataclasses import dataclass, fields
from typing import Any, Self, dataclass_transform


@dataclass_transform(kw_only_default=True, frozen_default=True)
def value_object[ClsT](cls: type[ClsT]) -> type[ClsT]:
    return dataclass(cls, frozen=True, slots=True, kw_only=True)


@value_object
class ValueObject(ABC):
    def __new__(cls, *_args: Any, **_kwargs: Any) -> Self:
        if cls is ValueObject:
            raise TypeError("Base ValueObject cannot be instantiated directly")
        if not fields(cls):
            raise TypeError(f"{cls.__name__} must have at least one field")
        return object.__new__(cls)
