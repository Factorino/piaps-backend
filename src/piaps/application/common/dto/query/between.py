import calendar
from datetime import date
from typing import Any, Protocol, Self

from piaps.application.common.dto.base import dto
from piaps.domain.errors.base import ValidationError


class _SupportsOrdering(Protocol):
    def __lt__(self, *args: Any, **kwargs: Any) -> bool: ...
    def __le__(self, *args: Any, **kwargs: Any) -> bool: ...
    def __gt__(self, *args: Any, **kwargs: Any) -> bool: ...
    def __ge__(self, *args: Any, **kwargs: Any) -> bool: ...


@dto
class Between[T: _SupportsOrdering]:
    value_from: T | None = None
    value_to: T | None = None

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if (
            self.value_from is not None
            and self.value_to is not None
            and self.value_from > self.value_to
        ):
            raise ValidationError("'from' value must be less than or equal to 'to' value")


class DateBetween(Between[date]):
    @classmethod
    def since(cls, period: date) -> Self:
        return cls(value_from=period)

    @classmethod
    def until(cls, period: date) -> Self:
        return cls(value_to=period)

    @classmethod
    def exact(cls, period: date) -> Self:
        return cls(value_from=period, value_to=period)

    @classmethod
    def for_month(cls, year: int, month: int) -> Self:
        last_day: int = calendar.monthrange(year, month)[1]
        return cls(
            value_from=date(year, month, 1),
            value_to=date(year, month, last_day),
        )
