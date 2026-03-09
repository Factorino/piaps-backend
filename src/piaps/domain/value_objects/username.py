import re
from typing import ClassVar

from piaps.domain.errors.base import ValidationError
from piaps.domain.value_objects.base import ValueObject, value_object


@value_object
class Username(ValueObject):
    _MIN_LENGTH: ClassVar[int] = 3
    _MAX_LENGTH: ClassVar[int] = 30
    _USERNAME_FMT: ClassVar[re.Pattern] = re.compile(r"^[a-z0-9]+$")

    value: str

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        stripped: str = self.value.strip()
        if not stripped:
            raise ValidationError("Invalid username: username must not be empty")

        if len(stripped) < self._MIN_LENGTH:
            raise ValidationError(
                f"Invalid username: username must be at least {self._MIN_LENGTH} characters"
            )

        if len(stripped) > self._MAX_LENGTH:
            raise ValidationError(
                f"Invalid username: username must not exceed {self._MAX_LENGTH} characters"
            )

        if not self._USERNAME_FMT.match(stripped):
            raise ValidationError("Invalid username: username contains invalid characters")

        object.__setattr__(self, "value", stripped)
