import re
from typing import ClassVar

from piaps.domain.errors.base import ValidationError
from piaps.domain.value_objects.base import ValueObject, value_object


@value_object
class FullName(ValueObject):
    _MAX_LENGTH: ClassVar[int] = 100
    _NAME_FMT: ClassVar[re.Pattern] = re.compile(r"^[a-zA-Zа-яА-ЯёЁ\-\s]+$")

    last_name: str
    first_name: str
    middle_name: str | None = None

    def __post_init__(self) -> None:
        self._validate_part("last_name", self.last_name)
        self._validate_part("first_name", self.first_name)
        if self.middle_name is not None:
            self._validate_part("middle_name", self.middle_name)

        object.__setattr__(self, "last_name", self.last_name.strip().title())
        object.__setattr__(self, "first_name", self.first_name.strip().title())
        if self.middle_name is not None:
            object.__setattr__(self, "middle_name", self.middle_name.strip().title())

    @property
    def full(self) -> str:
        parts: list[str] = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(parts)

    @property
    def short(self) -> str:
        initials: str = f"{self.first_name[0]}."
        if self.middle_name:
            initials += f"{self.middle_name[0]}."
        return f"{self.last_name} {initials}"

    def _validate_part(self, field: str, value: str) -> None:
        stripped: str = value.strip()
        if not stripped:
            raise ValidationError(f"Invalid full name format: {field} must not be empty")

        if len(stripped) > self._MAX_LENGTH:
            raise ValidationError(
                f"Invalid full name format: {field} must not exceed {self._MAX_LENGTH} characters"
            )

        if not self._NAME_FMT.match(stripped):
            raise ValidationError(f"Invalid full name format: {field} contains invalid characters")
