import re
from typing import ClassVar, Self

from piaps.domain.errors.base import ValidationError
from piaps.domain.value_objects.base import ValueObject, value_object


@value_object
class Code(ValueObject):
    UID_LENGTH: ClassVar[int] = 8
    _DELIMITER: ClassVar[str] = "-"
    _PREFIX_FMT: ClassVar[re.Pattern] = re.compile(r"^[A-Z]+$")

    prefix: str
    uid: str

    def __post_init__(self) -> None:
        self._validate()

    @classmethod
    def from_str(cls, code: str) -> Self:
        parts: list[str] = code.split(cls._DELIMITER, maxsplit=1)
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise ValidationError(
                f"Invalid code format: expected '<PREFIX><{cls._DELIMITER}><uid>'"
            )
        return cls(prefix=parts[0], uid=parts[1])

    @property
    def value(self) -> str:
        return f"{self.prefix}{self._DELIMITER}{self.uid}"

    def _validate(self) -> None:
        if not self._PREFIX_FMT.match(self.prefix):
            raise ValidationError(
                "Invalid code format: code prefix must be uppercase letters only"
            )

        if len(self.uid) != self.UID_LENGTH:
            raise ValidationError(
                f"Invalid code format: code uid must be {self.UID_LENGTH} characters"
            )
