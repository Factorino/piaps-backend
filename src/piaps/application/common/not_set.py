from typing import ClassVar, Literal, Self, TypeGuard


class NotSet:
    __instance: ClassVar[Self | None] = None

    def __new__(cls) -> Self:
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __repr__(self) -> Literal["NotSet"]:
        return "NotSet"

    def __bool__(self) -> Literal[False]:
        return False

    def __reduce__(self) -> str:
        return "NOTSET"


NOTSET = NotSet()


def is_set[T](value: T | NotSet) -> TypeGuard[T]:
    return value is not NOTSET
