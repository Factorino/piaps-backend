from decimal import ROUND_HALF_UP, Decimal
from typing import ClassVar

from piaps.domain.errors.base import ValidationError
from piaps.domain.value_objects.base import ValueObject, value_object


@value_object
class Money(ValueObject):
    _MAX_DIGITS: ClassVar[int] = 15
    _DECIMAL_PLACES: ClassVar[int] = 2
    _QUANTIZE_EXP: ClassVar[Decimal] = Decimal("0.01")

    value: Decimal

    def __post_init__(self) -> None:
        self._validate()

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        return Money(value=self.value + other.value)

    def __radd__(self, other: "Money") -> "Money":
        return self.__add__(other)

    def __sub__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        return Money(value=self.value - other.value)

    def __rsub__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        return Money(value=other.value - self.value)

    def __mul__(self, factor: Decimal) -> "Money":
        if not isinstance(factor, (Decimal, int)):
            return NotImplemented
        return Money(value=self.value * factor)

    def __rmul__(self, factor: Decimal) -> "Money":
        return self.__mul__(factor)

    def _validate(self) -> None:
        quantized: Decimal = self.value.quantize(self._QUANTIZE_EXP, rounding=ROUND_HALF_UP)
        integer_digits: int = len(str(quantized).replace("-", "").split(".")[0])
        max_integer_digits: int = self._MAX_DIGITS - self._DECIMAL_PLACES
        if integer_digits > max_integer_digits:
            raise ValidationError(
                f"Invalid money value: money value exceeds maximum of {max_integer_digits} "
                f"integer digits"
            )

        object.__setattr__(self, "value", quantized)
