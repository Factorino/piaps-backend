from dataclasses import field
import re
from typing import ClassVar

from piaps.domain.errors.base import ValidationError
from piaps.domain.value_objects.base import ValueObject, value_object


@value_object
class Password(ValueObject):
    _MIN_LENGTH: ClassVar[int] = 8
    _MAX_LENGTH: ClassVar[int] = 64
    _ALLOWED_FMT: ClassVar[re.Pattern] = re.compile(
        r"^[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]+$"
    )

    value: str = field(repr=False)

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if len(self.value) < self._MIN_LENGTH:
            raise ValidationError(
                f"Invalid password: must be at least {self._MIN_LENGTH} characters"
            )

        if len(self.value) > self._MAX_LENGTH:
            raise ValidationError(
                f"Invalid password: must not exceed {self._MAX_LENGTH} characters"
            )

        if not self._ALLOWED_FMT.match(self.value):
            raise ValidationError(
                "Invalid password: must contain only letters, digits, and special characters"
            )
