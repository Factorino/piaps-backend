from enum import IntEnum
from typing import Self


class UserRole(IntEnum):
    _label_: str

    EMPLOYEE = "employee"
    ACCOUNTANT = "accountant"
    ADMINISTRATOR = "administrator"

    def __new__(cls, label: str) -> Self:
        value: int = len(cls.__members__)
        member: Self = int.__new__(cls, value)
        member._value_ = value
        member._label_ = label
        return member

    @property
    def label(self) -> str:
        return self._label_
