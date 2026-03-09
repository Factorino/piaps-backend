import re
from typing import ClassVar

from piaps.domain.errors.base import ValidationError
from piaps.domain.value_objects.base import ValueObject, value_object


@value_object
class Name(ValueObject):
    _MAX_LENGTH: ClassVar[int] = 100
    _NAME_FMT: ClassVar[re.Pattern] = re.compile(r"^[a-zA-Zа-яА-ЯёЁ0-9\s.,!?;:()\-\"\']+$")

    value: str

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        stripped: str = self.value.strip()
        if not stripped:
            raise ValidationError("Invalid name: name must not be empty")

        if len(stripped) > self._MAX_LENGTH:
            raise ValidationError(
                f"Invalid name: name must not exceed {self._MAX_LENGTH} characters"
            )

        if not self._NAME_FMT.match(stripped):
            raise ValidationError("Invalid name: name contains invalid characters")

        object.__setattr__(self, "value", stripped)
