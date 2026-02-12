from piaps.domain.errors.base import ValidationError
from piaps.domain.value_objects.base import ValueObject, value_object


@value_object
class Period(ValueObject):
    year: int
    month: int

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if self.year < 1:
            raise ValidationError
        if not (1 <= self.month <= 12):
            raise ValidationError
